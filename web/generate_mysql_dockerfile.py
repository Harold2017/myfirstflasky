import os
from config import Config


# mysql initialization files
docker_file = 'Dockerfile'
source_dir = os.path.abspath(os.curdir)
destination_dir = os.path.join(source_dir, '../mysql')

# before creating files, check that the destination dir exists
if not os.path.isdir(destination_dir):
    os.mkdir(destination_dir)

# create the 'Dockerfile' for initializing mysql
with open(os.path.join(destination_dir, docker_file), 'w') as mysql_dockerfile:
    mysql_dockerfile.write('FROM mysql:5.7')
    mysql_dockerfile.write('\n')
    mysql_dockerfile.write('\n# Set environment variables')
    mysql_dockerfile.write('\nENV MYSQL_USER {}'.format(Config.MYSQL_USER))
    mysql_dockerfile.write('\nENV MYSQL_PASSWORD'.format(Config.MYSQL_PASSWORD))
    mysql_dockerfile.write('\nENV MYSQL_DB'.format(Config.MYSQL_DB))
    mysql_dockerfile.write('\n')
