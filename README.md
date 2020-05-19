# soccer-riddle

This is a small soccer quiz which uses transfermarkt.com to scrap soccer players.
The user can create games to challenge friends with their soccer knowledge and ask them to find the one player, which played together with the choosen player. It allows to show up to 7 teammates and for different difficulties the creater can allow jokers/helpfull information or not.

Currently the game is hosted on heroku.

The game can be found at: https://guesswho.games/


# useful commands

## Postregres Admin Panel
```heroku config:get DATABASE_URL -a soccer-riddle | xargs pgweb --url```

# Todo:
## Design:
* Fine Tune Design
<!-- * make mobile friendly (also cards, responsive font) -->
<!-- * change player card background -->
<!-- * Create Game, Player card image to big -->

## Bugs
* Handle POST requests (AJAXS)
<!-- * Get infos for selected mates from individual pages, not search -->
* Add minimum numbers of players

## Featues:
<!-- * add basic statistics on how much played -->
<!-- * restrict joker -->
* get common clubs https://www.transfermarkt.de/mario-mandzukic/gemeinsameSpiele/spieler/34572
* add error handling 404 ...
* Add User management
* Add play against eachother mode
* Add next/prev quiz

<!-- * Sentry -->
* Share GuessWho on Footer
<!-- * share Whatsapp (Tried, lets see) -->