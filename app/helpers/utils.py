from app.models.games import EnumRole


def render_level(num):
    val = "primary"
    if EnumRole(num).name == "hard":
        val = "danger"
    elif EnumRole(num).name == "medium":
        val = "warning"
    return '<span class="badge badge-%s">%s</span>' % (val, EnumRole(num).name)


def replace_joker(player, joker):
    return_player = dict(
        img=player.img,
        age="??",
        name="???",
        position="??",
        nationality_img="",
        club_img="",
        visibility=30
    )
    if joker >= 1:
        return_player["age"] = player.age
    if joker >= 2:
        return_player["position"] = player.position
    if joker >= 3:
        return_player["nationality"] = player.nationality
        return_player["nationality_img"] = player.nationality_img
    if joker == 4:
        return_player["visibility"] = 7
    return return_player
