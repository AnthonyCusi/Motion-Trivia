import json
import urllib.parse
import urllib.request
import urllib.error

def get_data(url: str) -> dict:
    '''Takes URL and returns dictionary representing the JSON response'''

    response = None
    try:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        json_string = response.read().decode(encoding = "utf-8")

        return json.loads(json_string)

    except urllib.error.HTTPError as error_val:
        print("FAILED")
        print(error_val.code, url)
        print("NOT 200")
        return "quit"

    except urllib.error.URLError:
        print("FAILED")
        print(url)
        print("NETWORK")
        return "quit"

    except json.decoder.JSONDecodeError:
        print("FAILED")
        print(response.getcode(), url)
        print("FORMAT")
        return "quit"

    finally:
        if response != None:
            response.close()


def get_session_data():
    '''Returns session information including token'''
    return dict(get_data('https://opentdb.com/api_token.php?command=request'))


def get_game_data(token):
    '''Returns question/answer information'''
    return dict(get_data('https://opentdb.com/api.php?amount=10&type=boolean&token=' + token))


def reset_token(token):
    get_data('https://opentdb.com/api_token.php?command=reset&token=' + token)
