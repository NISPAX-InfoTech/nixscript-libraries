# Official NixScript Libraries

This public repository is the official library registry used by the NixScript CLI commands `nix install` and `nix update`.

## Install a library

From a NixScript installation with `curl` available:

```sh
nix install numbers
nix list
```

Then import it in a script:

```ns
use numbers;

nix main() {
    println(clamp(12, 0, 10)); // 10
}
```

## Registry format

- `index.txt` lists the current version of each official package, one entry per line: `name MAJOR.MINOR.PATCH`.
- A package named `numbers` at version `1.0.0` is stored at `libraries/numbers/1.0.0/numbers.ns`.
- Package names are lowercase identifiers, up to 64 characters, beginning with a letter and containing only lowercase letters, digits, or underscores.
- Keep released version directories immutable. To publish an update, add a new version directory and update the corresponding version in `index.txt`.
- The initial registry format supports one NixScript source file per package. Dependencies and integrity signatures are not part of this version of the format.

Only publish libraries intended to be distributed as official NixScript packages. Review source changes carefully before updating the registry index.
