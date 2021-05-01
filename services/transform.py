import os
import numpy as np
import pandas as pd


class Transform:

    def __init__(self, filename, local_path, new_filename, header, header_list, columns):
        self.filename = filename
        self.local_path = local_path
        self.new_filename = new_filename
        self.header = header
        self.header_list = header_list
        self.columns = columns

    def transform(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if (dir_path != self.local_path):
            os.chdir(self.local_path)

        df = pd.read_csv(self.local_path + self.filename)
        df = df.replace({np.nan: ''})

        # Set header if no header
        if self.header == True:
            df = pd.read_csv(self.local_path + self.filename, dtype=str)
        else:
            df = pd.read_csv(self.local_path + self.filename, names=self.header_list, dtype=str)

        # Map, create, build, and order columns
        column_keys = self.columns.keys()
        if 'map' in column_keys:
            df = df.rename(columns=self.columns['map'])

        if 'create' in column_keys:
            for key, value in list(self.columns['create'].items()):
                df[key] = value

        if 'build' in column_keys:
            size = len(self.columns['build'])

            for i in range(size):
                for new_column, build in list(self.columns['build'][i].items()):
                    column_name = build['column']
                    steps_size = len(build['steps'])

                    for j in range(steps_size):
                        if 'slice' in build['steps'][j]:
                            value = build['steps'][j]['slice']
                            df[new_column] = eval(f'df[column_name].str{value}')

                        elif 'replace' in build['steps'][j].keys():
                            value = build['steps'][j]['replace']
                            pat = value.get('pat', '')
                            repl = value.get('repl', '')
                            regex = value.get('regex', True)

                            if regex == False:
                                df[column_name] = eval(
                                    f'df[\'{column_name}\'].str.replace(\'{pat}\', \'{repl}\', regex=False)')
                            else:
                                df[column_name] = eval(
                                    f'df[\'{column_name}\'].str.replace({pat}, \'{repl}\')')

                        elif 'format' in build['steps'][j].keys():
                            value = build['steps'][j]['format']
                            df[column_name] = eval(
                                f'df[\'{column_name}\'].astype(int).map(\'{value}\'.format)')

                        elif 'pre_append' in build['steps'][j]:
                            value = build['steps'][j]['pre_append']
                            df[new_column] = value + df[new_column]

                        elif 'post_append' in build['steps'][j]:
                            value = build['steps'][j]['post_append']
                            df[new_column] = df[new_column] + value

                        elif 'column_append' in build['steps'][j]:
                            value = build['steps'][j]['column_append']
                            if not new_column in df.columns:
                                df[new_column] = ''
                            df[new_column] = df[new_column] + value + df[column_name]

                        elif 'select' in build['steps'][j]:
                            value = build['steps'][j]['select']
                            column_op = column_name
                            df = eval(f'df.loc[ df[new_column] {column_op} \'{value}\' ]')

                        else:
                            print('Invalid step attempted')

        if 'order' in column_keys:
            df = df[self.columns['order']]

        # Write to file CSV
        df.to_csv(self.new_filename, index=False)