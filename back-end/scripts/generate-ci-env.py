import os
import secrets

import click


@click.command()
@click.option(
    "--out", "-o", default="src/config/.env", help="Location to store .env file in"
)
def main(out) -> None:
    """Within Github Actions, read in the
    environment variables supplied. Then,
    convert the environment variables to
    a .env file that the app can load.

    This is done pretty much because we
    don't have access to the Secrets function
    in the repository.

    For secret key, for now it will be
    hard coded. This should not matter because
    the secret key will be only for CI testing
    on a temporary test database.

    :param out: Path to store .env file in
    :type out: PathLike
    """
    # Read in environments
    envs = {
        f"TEST_{key}": value
        for key, value in os.environ.items()
        # if key in global_config
    }

    # Set fake secret key
    # should be the same as `openssl rand -hex 32`
    envs["SECRET_KEY"] = secrets.token_hex(32)
    envs["ALGORITHM"] = "HS256"
    with open(out, "w") as f:
        for key, value in envs.items():
            f.write(f"{key}={value}\n")
    print("Set up .env file for")


if __name__ == "__main__":
    main()
