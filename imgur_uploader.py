import os

import click
from imgurpython import ImgurClient

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


def get_config():
    client_id = os.environ.get("IMGUR_API_ID")
    client_secret = os.environ.get("IMGUR_API_SECRET")
    refresh_token = os.environ.get("IMGUR_REFRESH_TOKEN")

    config = ConfigParser.ConfigParser()
    config.read([os.path.expanduser("~/.config/imgur_uploader/uploader.cfg")])

    try:
        imgur = dict(config.items("imgur"))
    except:
        imgur = {}

    client_id = client_id or imgur.get("id")
    client_secret = client_secret or imgur.get("secret")
    refresh_token = refresh_token or imgur.get("refresh_token", "")

    if not (client_id and client_secret):
        return {}

    data = {"id": client_id, "secret": client_secret}
    if refresh_token:
        data["refresh_token"] = refresh_token
    return data


@click.command()
@click.argument("images", type=click.Path(exists=True), nargs=-1)
def upload_image(images):
    """Uploads image files to Imgur"""

    config = get_config()

    if not config:
        click.echo(
            "Cannot upload - could not find IMGUR_API_ID or " "IMGUR_API_SECRET environment variables or config file"
        )
        return

    if "refresh_token" in config:
        client = ImgurClient(config["id"], config["secret"], refresh_token=config["refresh_token"])
        anon = False
    else:
        client = ImgurClient(config["id"], config["secret"])
        anon = True

    links = []
    copylink = True
    
    try:
        import pyperclip
    except ImportError:
        copylink = False
        
    for image in images:
        click.echo("Uploading file {}".format(click.format_filename(image)))

        response = client.upload_from_path(image, anon=anon)

        click.echo("File uploaded - see your image at {}".format(response["link"]))
        
        if copylink:
            # add individual link to clipboard
            links.append(response["link"])
            pyperclip.copy(response["link"])
    
    if copylink:
        # add all links to the clipboard
        # useful if user does not have a clipboard manager with history
        pyperclip.copy("\n".join(links))
    else:
        print("pyperclip not found. To enable clipboard functionality, please install it.")
  

if __name__ == "__main__":
    upload_image()
