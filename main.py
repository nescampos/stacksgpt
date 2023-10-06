from waitress import serve
from flask import Flask, jsonify, request, send_from_directory
import requests


class StacksGPTPlugin:

  # Define the constructor for the class
  def __init__(self, base_url):
    # Initialize the base_url attribute
    self.base_url = base_url

  def get_balance(self, account_id):
    # Define the endpoint for the balance API
    endpoint = f"/extended/v1/address/{account_id}/balances"

    # Construct the full URL for the API request
    url = f"{self.base_url}{endpoint}"

    balance_info = self.query_mirror_node_for(url)

    if balance_info is not None:

      stx_balance = balance_info["stx"]

      tBalance = float(stx_balance["balance"]) / (10**6)
        
      return tBalance

    # Return None if the query is wrong or if the account or token was not found
    return None

  def query_mirror_node_for(self, url):
    # Make a GET request to the mirror node REST API
    headers = {'Accept': "application/json"}
    
    info = requests.get(url, headers=headers)
    # Check if the response status code is 200 (OK)
    if info.status_code == 200:
      # Parse the token info JSON response data
      info_data = info.json()
      return info_data
    else:
      # Return None if mirror node query is wrong or unsuccessful
      return None


# Initialize the plugin with the mainnet base URL
plugin = StacksGPTPlugin("https://api.mainnet.hiro.so")

# Create the Flask web server
app = Flask(__name__)


@app.route('/get_balance', methods=['GET'])
def get_balance():
  # Use query parameter 'account_id' to specify the account ID
  account_id = request.args.get('account_id', '')
  token_balance = plugin.get_balance(account_id)
  if token_balance is not None:
    return jsonify({'account_id': account_id, 'token_balance': token_balance})
  else:
    return jsonify({
      'error':
      'Could not get the STX balance for this account. Please check again.'
    }), 404


@app.route("/.well-known/ai-plugin.json", methods=['GET'])
def serve_ai_plugin():
  return send_from_directory(app.root_path,
                             'ai-plugin.json',
                             mimetype='application/json')


@app.route("/openapi.yaml", methods=['GET'])
def serve_openapi_yaml():
  return send_from_directory(app.root_path,
                             'openapi.yaml',
                             mimetype='text/yaml')


if __name__ == "__main__":
  serve(app, host="0.0.0.0", port=5000)

