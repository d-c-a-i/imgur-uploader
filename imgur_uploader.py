import os

import click
from imgurpython import ImgurClient

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import argparse



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
@click.argument("path", type=click.Path(exists=False), nargs=1)
def upload_image(images, path):
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
    
        
    for image in images:
        click.echo("Uploading file {}".format(click.format_filename(image)))

        response = client.upload_from_path(image, anon=anon)

        click.echo("File uploaded - see your image at {}".format(response["link"]))


        import os.path
        import numpy as np
        if os.path.isfile(path):
            matching_dic = np.load(path, allow_pickle=True)[()]
            matching_dic[image] = response["link"]
            size = len(matching_dic.values())

        else:
            matching_dic = {}
            matching_dic[image] = response["link"]
            size = len(matching_dic.values())
        np.save(path, matching_dic)
        print(f'{size} image-url pairs in dictionary')



        
  

if __name__ == "__main__":
    upload_image()