from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, \
    CommentForm, EditSensorForm, SelectSensorForm, DeleteSensorForm, AddSensorForm, \
    NoSensorForm
from .. import db
from ..models import User_photos
from ..models import Permission, Role, User, Post, Comment, Sensors, Sensor_data
from ..decorators import admin_required, permission_required
from werkzeug.utils import secure_filename
import os
from pyecharts import Line
from pytz import timezone
from flask_table import Table, Col


tzchina = timezone('Asia/Shanghai')
utc = timezone('UTC')


class ItemTable(Table):
    name = Col('Name')
    id = Col('id')
    classes = ['table', 'table-bordered']
    about_sensor = Col('about_sensor')
    timestamp = Col('UTC_timestamp')


class Item(object):
    def __init__(self, name, id, about_sensor, timestamp):
        self.name = name
        self.id = id
        self.about_sensor = about_sensor
        self.timestamp = timestamp


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if User_photos.query.filter_by(author_id=user.id).first():
        photo = User_photos.query.filter_by(author_id=user.id).order_by(User_photos.id.desc()).first()
        filename = os.path.basename(photo.file_path)
    else:
        filename = None
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, filename=filename, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        if form.photo.data:
            f = form.photo.data
            filename = secure_filename(f.filename)
            file_path = os.path.join(
                os.path.abspath("app/static/images"), filename)
            f.save(file_path)
            user_photo = User_photos(author_id=current_user.id)
            user_photo.file_path = file_path
            db.session.add(user_photo)
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/edit-sensor', methods=['GET', 'POST'])
@login_required
def edit_sensor():
    user = current_user
    if Sensors.query.filter_by(author_id=user.id).first():
        sensors = Sensors.query.filter_by(author_id=user.id).order_by(Sensors.id.desc()).all()
        form = EditSensorForm(sensors)
        warn = 0
        table = ItemTable(sensors)
    else:
        warn = 'No sensors recorded.'
        form = NoSensorForm()
        table = 0
    if form.validate_on_submit():
        if form.add.data:
            return redirect(url_for('.add_sensor'))
        elif form.delete.data:
            return redirect(url_for('.delete_sensor'))
        else:
            pass
    return render_template('edit_sensor.html', warn=warn, form=form, table=table)


@main.route('/add-sensor', methods=['GET', 'POST'])
@login_required
def add_sensor():
    form = AddSensorForm()
    if form.validate_on_submit():
        sensor = Sensors(author_id=current_user.id)
        sensor.name = form.name.data
        sensor.about_sensor = form.about_sensor.data
        db.session.add(sensor)
        flash('Your sensor has been recorded.')
        return redirect(url_for('.edit_sensor'))
    return render_template('add_sensor.html', form=form)


@main.route('/delete-sensor', methods=['GET', 'POST'])
@login_required
def delete_sensor():
    user = current_user
    if Sensors.query.filter_by(author_id=user.id).first():
        sensors = Sensors.query.filter_by(author_id=user.id).order_by(Sensors.id.desc()).all()
        form = DeleteSensorForm(sensors)
        warn = 0
    else:
        warn = 'No sensors recorded.'
        form = NoSensorForm()
    if form.validate_on_submit():
        sensor = form.sensor.data
        sensor_d = Sensors.query.filter_by(id=sensor).first()
        sensor_data = Sensor_data.query.filter_by(sensor_id=sensor).all()
        for d in sensor_data:
            db.session.delete(d)
        db.session.delete(sensor_d)
        flash('Your sensor has been deleted.')
        return redirect(url_for('.edit_sensor'))
    return render_template('delete_sensor.html', warn=warn, form=form)


@main.route('/sensors/<username>', methods=['GET', 'POST'])
@login_required
def sensors(username):
    user = User.query.filter_by(username=username).first_or_404()
    if Sensors.query.filter_by(author_id=user.id).first():
        sensors = Sensors.query.filter_by(author_id=user.id).order_by(Sensors.id.desc()).all()
        form = SelectSensorForm(sensors, prefix="form")
        form2 = NoSensorForm(prefix="form2")
    else:
        sensors = 0
        form = NoSensorForm(prefix="form")
        form2 = NoSensorForm(prefix="form2")
    if form.validate_on_submit():
        sensor = form.sensor.data
        sensor_data = Sensor_data.query.filter_by(sensor_id=sensor).order_by(-Sensor_data.id.desc()).all()
        timestamp = []
        data = []
        for i in sensor_data:
            timestamp.append(i.timestamp.replace(tzinfo=utc).astimezone(tzchina).strftime('%Y/%m/%d-%H:%M:%S'))
            data.append(i.value)
        if len(data) is 0:
            return '''<div class="page-header">
                        <h2>No recorded data!</h2>
                    </div>'''
        else:
            s = Sensors.query.filter_by(id=sensor).first()
            title = s.name
            line = Line(title=title, width=800, height=400)
            attr = timestamp
            d = data
            line.add("data", attr, d, is_smooth=False, is_datazoom_show=True, mark_line=["average"],
                     mark_point=["min", "max"])
            line.render_embed()
            return render_template('sensor_render_pyecharts.html', chart=line.render_embed())
    else:
        if form2.validate_on_submit():
            return redirect(url_for('.add_sensor'))
        return render_template('sensors.html', user=user, sensors=sensors, form=form, form2=form2)
