# Twitchy

### A Python Twitch Bot

Twitchy is a customizable Twitch bot built using Python. This following information will help you set up pre-commit
hooks, configure
environment variables, and run the bot from the command line.

## Setting Environment Variables

To run Twitchy, you need to set up the `TWITCH_BOT` environment variable with the required parameters.

1. **Set the Environment Variable**:
    - The `TWITCH_BOT` environment variable must contain 6 comma-separated
      values: `username,channel,bot_name,oauth_token,client_id,client_secret`.

    - Example (Linux/MacOS):
        ```sh
        export TWITCH_BOT="username,channel,bot_name,oauth_token,client_id,client_secret"
        ```

    - Example (Windows):
        ```cmd
        set TWITCH_BOT=username,channel,bot_name,oauth_token,client_id,client_secret
        ```

## Running Twitchy from Command Line

If you prefer not to use environment variables, you can run Twitchy using command-line arguments.

1. **Run the Bot**:
    ```sh
    python -m twitchy <username> <channel> <bot_name> <oauth_token> <client_id> <client_secret>
    ```

    - Replace `<username>`, `<channel>`, `<bot_name>`, `<oauth_token>`, `<client_id>`, and `<client_secret>` with your
      actual Twitch credentials.

## Example Command

```sh
python -m twitchy my_username my_channel my_bot_name my_oauth_token my_client_id my_client_secret
```

# Requirements for Branching and Pull Requests

## Setting Up Pre-commit Hooks

To maintain code quality and consistency, we use `pre-commit` hooks with `black` for code formatting and `pylint` for
linting.

1. **Install Pre-commit**:
    ```sh
    pip install pre-commit
    ```

2. **Install the pre-commit hooks**:
    ```sh
    pre-commit install
    ```

3. **Run the pre-commit hooks manually (optional)**:
    ```sh
    pre-commit run --all-files
    ```
