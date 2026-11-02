# Archived bookshelf

Archived on 2026-11-02 at Gary's request. This directory is excluded from the
published site. The source is still visible in the public GitHub repository.

The directory mirrors the original paths for the page, data, layouts, include,
JavaScript, and real cover images. All eight books and the personal note, including
its bold emphasis, are preserved. The shelf styles are in
`assets/css/bookshelf.scss`.

To restore in a reviewed branch:

1. Copy the mirrored `_pages`, `_data`, `_layouts`, `_includes`, `assets/js`, and
   `assets/images` files back to the repository root. The archived page replaces
   the live `/bookshelf/` redirect.
2. Append `assets/css/bookshelf.scss` to the active `assets/css/main.scss`.
3. Add Bookshelf at `/bookshelf/` to `_data/navigation.yml`.
4. Restore the JavaScript syntax check if desired, then run source checks, the
   full Jekyll build, rendered-site checks, and responsive/interaction QA.

Keep this directory excluded from publication unless explicitly restoring it.
