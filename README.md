# Payment-API

 > An API for a crypto payment platform with a transaction processing system powered by workers.

## Requirements
 - Docker

## Development setup

 > Clone this repo and navigate into the project's directory


> Create a python3 virtual environment for the project and activate it.

#### Build app service image

```bash
  $ docker-compose build app
  $ docker tag <app service> app
```

#### Start up the server

```bash
$ docker-compose up --build
```

#### Run tests

 > Build the images with the test docker-compose file - docker-compose.test.yml

 > Run tests using the commands below:

```bash
$ docker-compose -f docker-compose.test.yml up --build
$ docker-compose -f docker-compose.test.yml run --rm  app sh -c "pytest -s --disable-warnings"
```

 >  The app should now be available from your browser at http://127.0.0.1:9000

 > Test API with Postman.

##### Endpoints

 > For endpoints that require authentication, add a valid access token to the Request *Authorization heade*r - *Bearer <ACCESS TOKEN>*

- **Home**

     *http://127.0.0.1:9000/*

- **Signup a user**

   POST */api/v1/auth/signup*

    > Request Payload
     
    ```
    {
        "name": <full name>,
        "email": <email>,
        "password": <password min_length 8>  
    }
    ```

-  **Login a user**

   POST */api/v1/auth/login*

    > Request Payload 
    
    ```
    {
        "email": <email>,
        "password": <password min_length 8>  
    }
    ```

- **Logout user** `[JWT token required]`

    POST */api/v1/logout*
    
- **setup wallet** `[JWT token required]`

    PUT */api/v1/account/<user_id>/walletSetup*
    
    > Request Payload 
    
    ```
    {
	    "description": <acccount description>,
	    "type": <"BTC" or "ETH">,
	    "amount": <amount>,
	    "max_amount": <maximum limit for transaction>
    }
    ```
    
- **Fund wallet** `[JWT token required]`

    PUT */api/v1/account/<user_id>/fundWallet*
    
    > Request Payload
    
    ```
    {
	    "type": <"BTC" or "ETH">,
	    "amount": <amount>
    }
    ```
    
- **Check account balance** `[JWT token required]`

    GET */api/v1/account/<user_id>/checkBalance?type=*
    
    > The query param *'type'* should be either *'ETH'* or *'BTC'*. The value is case-insenstive.
    
- **Make a transaction** `[JWT token required]`

    POST */api/v1/transaction/payment*
    
    > Request payload 
    
    ```
    {
        "source_wallet_id": <source_user_wallet_id>,
        "target_wallet_id": <target_user_wallet_id>,
        "type": <"BTC" or "ETH">,
        "amount": <amount>
    }
    ```
    
- **Check transaction status** `[JWT token required]`

    GET */api/v1/transaction/<transaction_id>/status*
    

- **Retrieve transaction history for a user** `[JWT token required]`

    GET */api/v1/transaction/<user_id>/history*
    
