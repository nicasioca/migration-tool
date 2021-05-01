# https://medium.com/@thapa.parmeshwor/sftp-upload-and-download-using-python-paramiko-a594e81cbcd8
from paramiko import Transport, SFTPClient
import time
import errno
import logging
logging.basicConfig(format='%(levelname)s : %(message)s',
                    level=logging.INFO)


class SftpClient:

    _connection = None

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.create_connection(self.host, self.port,
                               self.username, self.password)

    @classmethod
    def create_connection(cls, host, port, username, password):

        transport = Transport(sock=(host, port))
        transport.connect(username=username, password=password)
        cls._connection = SFTPClient.from_transport(transport)

    @staticmethod
    def uploading_info(uploaded_file_size, total_file_size):

        logging.info('uploaded_file_size : {} total_file_size : {}'.
                     format(uploaded_file_size, total_file_size))

    def upload(self, local_path, remote_path):

        # Set confirm to False to avoid matching uploaded size to original file size
        self._connection.put(localpath=local_path,
                             remotepath=remote_path,
                             callback=self.uploading_info,
                             confirm=False)

    def file_exists(self, remote_path):

        try:
            self._connection.stat(remote_path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            raise
        else:
            return True

    def download(self, remote_path, local_path, retry=5):

        if self.file_exists(remote_path) or retry == 0:
            self._connection.get(remote_path, local_path,
                                 callback=None)
        elif retry > 0:
            time.sleep(5)
            retry = retry - 1
            self.download(remote_path, local_path, retry=retry)

    def remove(self, remote_path, retry=5):

        if self.file_exists(remote_path) or retry == 0:
            self._connection.remove(remote_path)
        elif retry > 0:
            time.sleep(5)
            retry = retry - 1
            self.remove(remote_path, retry=retry)

    def close(self):
        self._connection.close()

if __name__ == '__main__':

    host,port = "",8022
    username,password = "",""

    client = SftpClient(host, port,
                        username, password)


    local_path = '/Users/nca/Desktop/migration-tool/'
    remote_path = '/outgoing/'

    file_name = ''
    print(f'Uploading file {file_name}')
    client.upload(f'{local_path}{file_name}',
            f'{remote_path}{file_name}')

    print(f'Downloading file {file_name}')
    client.download(f'{remote_path}{file_name}',
            f'{local_path}{file_name}')

    print(f'Removing file {file_name}')
    client.remove(f'{remote_path}{file_name}')


    client.close()