# Setting Up Anthropic API Key

## ⚠️ Security Warning
**NEVER commit your API key to the repository!** Always use environment variables.

## Method 1: Export in Terminal (Temporary)

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

This will only last for the current terminal session.

## Method 2: Add to Shell Profile (Permanent)

Add this line to your `~/.zshrc` (or `~/.bashrc` on Linux):

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Then reload:
```bash
source ~/.zshrc
```

## Method 3: Use .env File (Recommended for Development)

1. Create a `.env` file in the project root:
```bash
echo 'ANTHROPIC_API_KEY=your-api-key-here' > .env
```

2. The `.env` file is already in `.gitignore` so it won't be committed.

3. You can load it manually:
```bash
export $(cat .env | xargs)
```

## Verify It's Set

```bash
echo $ANTHROPIC_API_KEY
```

If it shows your key, you're good to go!

