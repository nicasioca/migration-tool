import os
import json
import numpy as np
import pandas as pd
import logging as log
log.basicConfig(level=log.INFO)

class TransformFile:

    def __init__(self, filename, local_path, new_filename, operation, pgp_recipient, pgp_passphrase, require_columns):
        self.filename = filename
        self.local_path = local_path
        self.new_filename = new_filename
        self.operation = operation
        self.pgp_recipient = pgp_recipient
        self.pgp_passphrase = pgp_passphrase
        self.require_columns = require_columns
        # self.validate_alias = validate_alias

    def transform(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if (dir_path != self.local_path):
            os.chdir(self.local_path)

        if self.operation == 'json':
            df = pd.read_csv(self.filename, dtype=str)
            df = df.replace({np.nan: ''})
            df.to_json(self.new_filename, orient='records')

        if self.operation == 'rename':
            os.rename(self.filename, self.new_filename)

        if self.operation == 'encrypt':
            os.system(f'gpg --output \"{self.new_filename}\" --encrypt --trust-model always --recipient \"{self.pgp_recipient}\" \"{self.filename}\"')

        if self.operation == 'decrypt':
            os.system(f'gpg --passphrase \"{self.pgp_passphrase}\" --output \"{self.new_filename}\" --decrypt \"{self.filename}\"')

        if self.operation == 'require':
            # Filter out the required column values
            df = pd.read_csv(self.filename, dtype=str)
            df = df.replace({np.nan: ''})
            require_columns = self.require_columns.split(',')
            log.info(f'Required size before: {len(df)}')
            for require_column in require_columns:
                df = df.loc[ df[require_column] != ""]
            log.info(f'Required size after: {len(df)}')
            df.to_csv(self.new_filename, index=False)

        if self.operation == 'validate':
            # Validate the file rows match the number of aliases
            df = pd.read_csv(self.filename, dtype=str)
            records = len(df)
            aliases = len(df[ df['cardNumber'].str.contains('tok_live_') ])
            log.info(f'# of records/rows in file: {records}')
            log.info(f'# of aliases in file: {aliases}')
            log.info(f'# of records/rows match the cardNumber aliases that start with tok_live_: {records == aliases}')

        if self.operation == 'csv':
            ext = os.path.splitext(self.filename)
            if (ext[1] == '.xlsx' or ext[1] == '.xls' or ext[1] == '.xlsm'):
                df = pd.read_excel(self.filename, dtype=str)
                df = df.replace({np.nan: ''})
                df.to_csv(self.new_filename, index=False)