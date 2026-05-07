from setuptools import setup, find_packages

setup(
    name="web_intel",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "firecrawl-py>=1.0.0",
        "scrapegraphai>=1.0.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "mcp>=1.0.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.10",
)
