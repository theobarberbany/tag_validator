# Tag Validator

A script to validate inputted tags.

optional arguments:
  -h, --help            show this help message and exit

  -f INPUTFILE, --file INPUTFILE
                        pass a file containing tags to be checked

  -d USER, --database USER
                        toggle database mode

  -m MANIFEST FILE, --manifest MANIFEST FILE
                        supply a manifest to check

database readonly user : warehouse_ro


## Deployment 

To deploy using docker and [vault](https://www.vaultproject.io/), build the image from the Dockerfile, or pull it from the docker hub: `tb15/tag_validator:master` 

The image will read the vault credentials from an environment variable, then use sed to edit the validator.py file to update the database credentials. You will need to pass the vault client token, server url and index within vault to the image.

e.g: 

```
docker run -d -it \
  -e TOKEN=${TOKEN} \
  -e URL=${VAULT_ADDR} \
  -e INDEX=tag-validator/db \
  tb15/tag_validator:master
  ```
  
  Then invoke the script:
  
  ```docker exec -it <container name> validator <commands>```
