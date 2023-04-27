# Imgur Migrate

Find all Imgur links in the markdown files under your directory, download them, and replace your Imgur links with wikilinks to local images.

## What it does

Suppose you have 1 Imgur links in `README.md` and 2 in `docs/System Design.md`:

```
.
├── README.md
└── docs
    └── System Design.md
```

becomes

```
.
├── README.md
├── README-1.png
└── docs
    ├── System Design.md
    ├── System Design-1.png
    └── System Design-2.png
```

In `docs/System Design.md` for example, it will replace `![text](https://i.imgur.com/123456.png)` with `![[System Design-1.png]]`, where the downloaded image name = `<markdown file name>-<auto-incremented number>`.

## How to run

Install

```
git clone https://github.com/dlccyes/imgur-migrate
sh install.sh
```

See usage (may take a while when running the first time)

```
imgur-migrate -h
```

Run it against the current directory

```
imgur-migrate
```

Or run it against a specific directory

```
imgur-migrate <path/to/your/directory>
```

Or run it against a specific file inside a directory

```
imgur-migrate <path/to/your/directory> <filename>
```

You can test it on the example directory in this repo.

```
imgur-migrate example
```

## Limitations

I create this simple tool for my own needs, so it isn't very featureful.

### Only works for markdown-style image links in markdow files

It will only search for markdown files, and only for Imgur links starting with `https://i.imgur.com/)` e.g. `https://i.imgur.com/123456.png` that are in `![]()` or `![text]()`. Meaning, if you have HTML-style embedded images in your markdown file, they won't be replaced.

### Does not escape codeblock

If your Imgur link is in codeblock or inline code, it will still be replaced.
