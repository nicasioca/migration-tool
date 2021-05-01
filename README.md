# migration-tool
> Migration tool

- Please read the general [Migration Process](https://www.verygoodsecurity.com/docs/guides/migrations)
- See example company below in order to generate the expected output files

## Required Installation
- Install GPG Suite: <https://gpgtools.org/>
- Install Brew: <https://brew.sh/>
- Install Python 3: `brew install python3`

## Setup Steps
1. Open a terminal, set the environmental variables in your Zshell profile
    - Find the your username (i.e. nca) in your path by typing `pwd` (i.e. /Users/nca)
    - Open your Zshell by running `open ~/.zshrc`
    - Add to the two lines below into your Zshell file, remember to update the VGS_PROCESS_FILES_PATH with your username
        ```
        export VGS_PROCESS_FILES_PATH=/Users/<YOUR USERNAME HERE>/Desktop/Migrations/PROCESS_FILES/
        export VGS_MIGRATION_FILE=$(date "+%Y-%m-%d")_VGS_
        ```
    - Refresh your terminal without closing it by running `exec zsh -l`

2. Create the folder `Migrations` on you desktop and `PROCESS_FILES` folder within that folder

3. Fork this repo (click fork in the top right of GitHub)

4. Clone repo locally from fork into your `PROCESS_FILES` folder

5. Set the upstream
    ```
    git remote add upstream git@github.com:nicasioca/migration-tool.git
    ```

6. Install required packages with requirements.txt file
    ```
    cd migration-tool
    pip install -r requirements.txt
    cd ..
    ```
    > NOTE: if you update the requirments.txt file
    ```
    pip install virtualenv
    cd migration-tool
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install <ENTER PYTHON PACKAGE HERE>
    pip freeze > requirements.txt
    deactivate
    cd ..
    ```
    > See https://docs.python-guide.org/dev/virtualenvs/

7. Before a PR, pull down the latest changes to your repo
    ```
    git pull --rebase upstream main
    ```

## Company Migration Steps

1. Open terminal within your `PROCESS_FILES` folder (see setup above)

2. Run the app server to handle services you require to transform files
    ```
    python ./migration-tool/app.py
    ```

3. Open another terminal within your `PROCESS_FILES` folder, set the standard Company fields with the first four temporary environmental variables and do not alter the rest
    > If a Profolio Company doesn't provide the Merchant ID (MID), then you can make a up dummy value like `companyName321` (50 characters or less)
    ```
    export DETAILS_MID=abc123
    export DETAILS_INPUTFILE=oe-edge-openedge.csv
    export DETAILS_OUTPUTFILE=edge_output_clear.json.pgp
    export DETAILS_OUTPUTFILE2=edge_output_alias.json

    export PROCESS_FILE_CSV=${DETAILS_INPUTFILE%.*}.csv
    export PROCESS_FILE_JSON=${DETAILS_INPUTFILE%.*}.json
    export PROCESS_FILE_TRANSFORMED=("${VGS_MIGRATION_FILE}transformed_${PROCESS_FILE_CSV}")
    export PROCESS_FILE_REQUIRED=("${VGS_MIGRATION_FILE}required_${PROCESS_FILE_CSV}")
    export PROCESS_FILE_ALIASED=("${VGS_MIGRATION_FILE}aliased_${PROCESS_FILE_CSV}")
    export PROCESS_FILE_REQUIRED_JSON=("${VGS_MIGRATION_FILE}required_${PROCESS_FILE_JSON}")
    ```

4. Run all the steps to transform an existing file to the expected Company CSV
    ```
    python ./migration-tool/cli.py transform --merchant_id $DETAILS_MID --filename $DETAILS_INPUTFILE --new_filename $PROCESS_FILE_TRANSFORMED &&
    python ./migration-tool/cli.py transform-file --operation require --filename $PROCESS_FILE_TRANSFORMED --new_filename $PROCESS_FILE_REQUIRED --columns 'previousTokenIdentifier,previousMerchantIdentifier,cardNumber,expirationYear,expirationMonth' &&
    cp $PROCESS_FILE_REQUIRED $PROCESS_FILE_ALIASED &&
    python ./migration-tool/cli.py sftp --request_type pgd --filename $PROCESS_FILE_ALIASED &&
    python ./migration-tool/cli.py transform-file --operation validate --filename $PROCESS_FILE_ALIASED
    ```
    > Checkpoint 1: Verify the PROCESS_FILE_REQUIRED and PROCESS_FILE_ALIASED look correct in CSV form (remember to check the validate response on the server for matching rows and aliases)

5. Convert the files from CSV to JSON
    ```
    python ./migration-tool/cli.py transform-file --operation json --filename $PROCESS_FILE_REQUIRED --new_filename $PROCESS_FILE_REQUIRED_JSON &&
    python ./migration-tool/cli.py transform-file --operation json --filename $PROCESS_FILE_ALIASED --new_filename $DETAILS_OUTPUTFILE2
    ```
    > Checkpoint 2: Make sure you used the aliased file for the DETAILS_OUTPUTFILE2 environmental variable and verify the required clear file and aliased file are in JSON form

6. Complete the encryption of the clear file and upload the files
    ```
    python ./migration-tool/cli.py transform-file --operation encrypt --pgp_recipient company-operations  --filename $PROCESS_FILE_REQUIRED_JSON --new_filename $DETAILS_OUTPUTFILE &&
    python ./migration-tool/cli.py sftp --request_type put --filename $DETAILS_OUTPUTFILE &&
    python ./migration-tool/cli.py sftp --request_type put --filename $DETAILS_OUTPUTFILE2
    ```
    > Checkpoint 3: Verify file sizes match by logging into the external SFTP and running on the SFTP terminal `ls -al` and seeing locally on you computer by running on the same SFTP terminal `lls -al`

## Future CLI Commands
I recommend adding the additional commands since they are all required in processing a migration.

- TODO 1: Add a create_test_file command to generate a test file automatically based on the PSP within the `cofig-test` folder, see examples within the `config-test/examples` folder
  <https://faker.readthedocs.io/en/master/providers/faker.providers.credit_card.html>

- TODO 2: Add a create_pgp_keys command to handle creating the asynchronous encryption keys, which is a public key and a private key customers usually desire to encrypt the files with (can provide to them in a password protected zip folder `zip -er FILENAME.zip FILESorFOLDERStoCOMPRESS`)
  <https://docs.github.com/en/github/authenticating-to-github/generating-a-new-gpg-key>