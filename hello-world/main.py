from threatpatrols.github_action import GithubInput, GithubSummary

github_summary = GithubSummary()


def main():
    hello_world = GithubInput("hello_world", github_summary).get(default=None)
    message = f"Hello {hello_world!r} this is the World!"
    print(message)
    github_summary.write(sort_lines=True)


if __name__ == "main":
    main()
