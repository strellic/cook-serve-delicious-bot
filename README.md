# cook-serve-delicious bot
My custom bot for the game Cook Serve Delicious.

It takes a screenshot of the game, then uses OCR to try and extract the recipe name. If the recipe name is found inside of `recipes.json`, it'll emulate the keystrokes and delays to cook the recipe.

The bot keeps track of recipes which are cooking, and will finish them automatically. It also knows in which order recipes come in, and it'll try to choose the recipes in the right order so that none run out of time.

### Limitations
* Doesn't work for baked potatoes