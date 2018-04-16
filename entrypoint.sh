#!/bin/bash

# ------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------

[[ -z ${TOKEN} ]] && echo "A valid TOKEN for accessing Vault was not specified in the environment." && exit 1
[[ -z ${URL} ]] && echo "A valid URL for accessing Vault was not specified in the environment." && exit 1
[[ -z ${INDEX} ]] && echo "A valid INDEX name for reading Vault secrets." && exit 1

# -----------------------------------------------------------
# Fetch Configuration From Vault
# -----------------------------------------------------------

override() {

    # $1 the remote key to fetch from vault
    # $2 the identifier in the file to replace with the value fetched from vault

    echo "Vault Lookup: ${URL}/v1/secret/${INDEX}/$1 : $2"
    json=$(curl -sH "X-Vault-Token:$TOKEN" -XGET ${URL}/v1/secret/${INDEX}/$1)
    if [[ $? -eq 0 ]]; then
        value=$(echo $json | jq -r .data.value)
        [[ "${value}" != "null" ]] && echo "Vault Lookup: Override found for $2" && echo "${value}" && \
        sed -i "s/$2/${value}/g" validator.py 
    fi

}

override db_port DBPORT
override db_name DBNAME
override db_host DBHOST

/bin/sh -c tail -f /dev/null
