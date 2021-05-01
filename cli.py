import click
import json
import os
import requests


def select(local_path, config_folder):
    # List of config formats
    path_config_folder = local_path + 'migration-tool/' + config_folder
    config_list = os.listdir(path_config_folder)
    try:
        config_list.remove('.DS_Store')
    except:
        pass

    config_list = list(map(lambda x: x.replace('.json',''),config_list))
    sorted_list = sorted(config_list)
    for config in sorted_list:
        print(f'{config}')

    # Accept config format
    config = ''
    val = input('Enter config: ')
    if val in sorted_list:
        with open(f'{path_config_folder}/{val}.json') as f:
            config = json.load(f)
    else:
        print('Invalid config!')
        exit()

    return config

@click.group()
def main():
    pass

# @main.command()
# def create_test_file(local_path):
#     """test a fake payment processor file"""
    # python ./migration-tool/cli.py test

    # config = select(local_path, 'test')
    ## TODO make fake data on server
    ## https://faker.readthedocs.io/en/master/providers/faker.providers.credit_card.html
    # url_format = 'http://localhost:5000/test'

@main.command()
@click.option('--request_type', required=True)
@click.option('--filename', required=True)
@click.option('--password', required=True, prompt="Please enter the SFTP password", hide_input=True)
@click.option('--local_path', required=True, envvar='VGS_PROCESS_FILES_PATH', type=click.Path(exists=True))
@click.option('--remote_path')
def sftp(request_type, filename, password, local_path, remote_path):
    """put, get, delete, or pgd (put, get, and delete) a file"""

    url_format = 'http://localhost:5000/sftp'

    sftp_config = select(local_path, 'config-sftp')
    sftp_config['request_type'] = request_type
    sftp_config['filename'] = filename
    sftp_config['password'] = password
    sftp_config['local_path'] = local_path

    json_payload = { "sftp": sftp_config }
    response = requests.post(url_format, json=json_payload)
    click.echo(response.json())

@main.command()
@click.option('--merchant_id', required=True)
@click.option('--filename', required=True)
@click.option('--new_filename', required=True)
@click.option('--local_path', required=True, envvar='VGS_PROCESS_FILES_PATH', type=click.Path(exists=True))
def transform(merchant_id, filename, new_filename, local_path):
    """transform a file based on processor to Company required file"""

    url_format = 'http://localhost:5000/transform'

    transform_confg = select(local_path, 'config-transform')

    columns = json.loads(transform_confg['columns'])
    columns['create']['previousMerchantIdentifier'] = merchant_id
    transform_confg['columns'] = json.dumps(columns)

    transform_confg['local_path'] = local_path
    transform_confg['filename'] = filename
    transform_confg['new_filename'] = new_filename

    json_payload = { "transform": transform_confg }
    response = requests.post(url_format, json=json_payload)
    click.echo(response.json())

@main.command()
@click.option('--filename', required=True)
@click.option('--new_filename', default='')
@click.option('--operation', required=True)
@click.option('--pgp_recipient', default='')
@click.option('--pgp_passphrase', default='')
@click.option('--columns', default='[]')
@click.option('--local_path', required=True, envvar='VGS_PROCESS_FILES_PATH', type=click.Path(exists=True))
def transform_file(filename, new_filename, operation, pgp_recipient, pgp_passphrase, columns, local_path):
    """confirm required values are in each row of the file"""

    url_format = 'http://localhost:5000/transform-file'

    transform_file_confg = {"filename": filename, "local_path": local_path, "new_filename": new_filename, "operation": operation, "pgp_recipient": pgp_recipient, "pgp_passphrase": pgp_passphrase, "require_columns": columns}

    json_payload = { "transform_file": transform_file_confg }
    response = requests.post(url_format, json=json_payload)
    click.echo(response.json())

if __name__ == '__main__':
    main()