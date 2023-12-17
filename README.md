# Steam Account Checker

This program check if the steam account is valid or not

## installation guide 

    pip install -r requirements.txt

Setting up `playwright drivers`   
    
    playwright install

Setup txt file

create the `login.txt` file with this format 

    User1:pass
    User2:pass
    User3:pass
    
create the proxy txt file with this format

    228.231.104.101:80
    159.138.255.141:9981
    222.104.128.205:48678
    154.236.191.46:1981

or this format 

    http://72.10.164.178:2041
    socks4://14.241.241.185:4145
    socks5://109.245.231.73:8192

Start main.py