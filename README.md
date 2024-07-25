# ENS Card Maker - Web Version
This repo is based on [littlebitstudios/ENSCardMaker](https://github.com/littlebitstudios/ENSCardMaker), but it runs a Flask web server that generates the same cards as the original.

# Usage
I will be hosting the app at https://enscards.littlebitstudios.com.<br>
Just go to `https://enscards.littlebitstudios.com/[user]` to get a card.<br>
`[user]` can be an ENS name (someone.eth) or ETH address (0xXXXX...XXXX).

Here's mine:

![card](https://enscards.littlebitstudios.com/littlebit670.eth)

You can also self-host the app using your own Docker instance:
```yaml
# example compose.yml file
version: '3.8'

services:
  main:
    image: ghcr.io/littlebitstudios/enscardmakerweb:main
    ports:
      - "5000:5000" # change the port if you want
    restart: unless-stopped
```

# Credits/Licensing
The font used for generating the cards is Inter by Rasmus Andersson, licensed under the [Open Font License](https://openfontlicense.org). Download the font from [Google Fonts](https://fonts.google.com/specimen/Inter).

ENS (the brand) is owned by ENS Labs Limited.

My code in this repository is licensed under the MIT License.
