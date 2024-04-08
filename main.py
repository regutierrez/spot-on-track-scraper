import os
import re
from dotenv import load_dotenv
import time
import requests
from bs4 import NavigableString, Tag
from bs4 import BeautifulSoup as bs

load_dotenv()


def spotontrack_login(username: str, password: str) -> requests.Session:
    # MIGHT BE BETTER TO MAKE A SEPARATE FUNCTION FOR CREATING A NEW SESSION

    login_url: str = "https://www.spotontrack.com/login"
    # might need to add this as arg for session.get in the future
    """
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/89.0.142.86"
    )

    headers: dict[str, str] = {"User-Agent": user_agent}
    """

    session: requests.Session = requests.Session()
    response_content: bytes | None = session.get(login_url)._content
    if response_content is None:
        raise Exception("Website HTML contents not found. Quitting script")

    print("session established successfully! finding auth token for login")
    html: bs = bs(response_content, "html.parser")
    auth_token_tag: Tag | NavigableString | None = html.find(
        "input", attrs={"name": "_token"}
    )

    if isinstance(auth_token_tag, Tag):
        auth_token: str = auth_token_tag.attrs["value"]
    else:
        raise Exception(
            "HTML tag where token is located was not found. Quitting script..."
        )

    if auth_token is None or auth_token == "":
        raise Exception("CSRF token not found. Quitting script...")

    print("successfully found auth token! logging in...")
    payload: dict[str, str] = {
        "email": username,
        "password": password,
        "_token": auth_token,
    }

    login = session.post(login_url, data=payload)

    if login.status_code != 200:
        raise Exception("Login failed. Quitting script...")

    print("login successful! proceeding with scraping...")
    return session


def convert_urls_to_api_urls(urls: list[str]) -> list[str]:
    api_urls: list[str] = []
    for url in urls:
        # https://www.spotontrack.com/api/tracks/.../current/apple is the api url we want
        api_url: str = re.sub("tracks", "api/tracks", url)
        api_url = api_url + "/current/apple"
        api_urls.append(api_url)
    print("urls converted to api urls\n", api_urls)
    return api_urls


def scrape_countries_from_url(session: requests.Session, playlist_urls: list[str]):
    api_urls: list[str] = convert_urls_to_api_urls(playlist_urls)
    playlist_countries_strings: list[str] = []

    for url in api_urls:
        print(f"scraping countries from url: {url}\nPlease wait...")
        # preventative measure to avoid being blocked by spotontrack
        time.sleep(15)
        print("requesting connection to api URL...")
        url_json: requests.Response = session.get(url)
        if url_json.status_code != 200:
            raise Exception("Request failed. Please check API URL. Quitting script...")
        playlists: list = url_json.json()["appleCurrent"]
        for pl in playlists:
            try:
                playlist_name: str = pl["playlist"]["name"]
                countries: list[str] = [
                    ct["country"]["code"].upper() for ct in pl["countries"]
                ]
                print(f"{len(countries)} countries found for playlist: {playlist_name}")
                countries_string: str = ",".join(countries)
                playlist_countries_strings.append(
                    f"{playlist_name}\n{countries_string}"
                )
            except Exception as e:
                print(
                    "There is something wrong while navigating the json file. Please see error details\n",
                    e,
                )
        print("done scraping countries from url: ", url)
        print("====================================")

    print("done scraping countries from urls...\n")
    return playlist_countries_strings


def write_to_file(urls: list[str], playlist_countries: list[str]) -> None:
    print("writing data to output.txt...")
    with open("output.txt", "w") as f:
        for url in urls:
            f.write("=======SONG=======\n")
            f.write(f"{url}\n")
            for pc_string in playlist_countries:
                f.write(f"{pc_string}\n\n")
        f.write("\n")


def main():
    username: str | None = os.getenv("SPOTONTRACK_USERNAME")
    password: str | None = os.getenv("SPOTONTRACK_PASSWORD")

    if username is None or password is None:
        raise Exception("Credentials not found. Please check env file.")
        exit()

    try:
        session: requests.Session = spotontrack_login(username, password)
    except Exception as e:
        raise Exception(e)

    playlist_urls: str | None = os.getenv("PLAYLIST_URLS")

    if playlist_urls is None:
        raise Exception("Playlist URLs not found. Please check env file.")
    else:
        playlist_urls_list: list[str] = playlist_urls.split(",")

    write_to_file(
        playlist_urls_list, scrape_countries_from_url(session, playlist_urls_list)
    )


if __name__ == "__main__":
    main()
