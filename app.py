from flask import Flask, request, make_response, jsonify
import json
from services.transform_file import TransformFile
from services.transform import Transform
from services.sftp import SftpClient

app = Flask(__name__)


def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/transform-file', methods=['OPTIONS', 'GET', 'POST'])
def transform_file():

    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        payload = request.json
        transform_file = payload['transform_file']

        # transform_file dict should be filename, local_path...in that order
        transform_file_list = list(transform_file.values())

        filename, local_path, new_filename, operation, pgp_recipient, pgp_passphrase, require_columns = transform_file_list
        t = TransformFile(filename, local_path, new_filename, operation, pgp_recipient, pgp_passphrase, require_columns)
        t.transform()

        return build_actual_response(jsonify({'success':True, 'message':'Processing job complete!'}))

    return build_actual_response(jsonify({'success':False, 'message':'Did not complete job.'}))

@app.route('/transform', methods=['OPTIONS', 'GET', 'POST'])
def transform():

    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        payload = request.json
        transform = payload['transform']

        # Transform dict should be filename, local_path...in that order
        transform_list = list(transform.values())

        filename, local_path, new_filename, header, header_list, columns = transform_list

        if header_list != '':
            header_list = header_list.replace(' ', '').split(",")
        else:
            header_list = []

        if columns != '' or columns != '{}':
            columns = json.loads(columns)
        else:
            return build_actual_response(jsonify({'success':False, 'message':'Valid column value required to compelete job!'}))

        t = Transform(filename, local_path, new_filename, header, header_list, columns)
        t.transform()

        return build_actual_response(jsonify({'success':True, 'message':'Processing job complete!'}))

    return build_actual_response(jsonify({'success':False, 'message':'Did not complete job.'}))

@app.route('/sftp', methods=['OPTIONS', 'GET', 'POST'])
def sftp():

    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        payload = request.json
        sftp = payload['sftp']

        # SFTP dict should be request_type, port, host...in that order
        sftp_list = list(sftp.values())
        filter_sftp_input = len([val for val in sftp_list if val != ''])

        if filter_sftp_input != 8:
            print('REQUIRED: request_type, port, host, username, password, filename, local_path, and remote_path!')
        else:
            request_type, port, host, username, password, filename, local_path, remote_path = sftp_list
            client = SftpClient(host, int(port),
                                username, password)

            if request_type == 'pgd':
              print(f'Uploading file {filename}')
              client.upload(f'{local_path}{filename}',
                    f'{remote_path}{filename}')
              print(f'Downloading file {filename}')
              client.download(f'{remote_path}{filename}',
                    f'{local_path}{filename}')
              print(f'Removing file {filename}')
              client.remove(f'{remote_path}{filename}')

            if request_type == 'put':
              print(f'Uploading file {filename}')
              client.upload(f'{local_path}{filename}',
                    f'{remote_path}{filename}')

            if request_type == 'get':
              print(f'Downloading file {filename}')
              client.download(f'{remote_path}{filename}',
                    f'{local_path}{filename}')

            if request_type == 'delete':
              print(f'Removing file {filename}')
              client.remove(f'{remote_path}{filename}')

        try:
            return build_actual_response(jsonify({'success':True, 'message':'Processing job complete!'}))
        finally:
            client.close()

    return build_actual_response(jsonify({'success':False, 'message':'Did not complete job.'}))

if __name__ == '__main__':
    app.run(debug=True)
