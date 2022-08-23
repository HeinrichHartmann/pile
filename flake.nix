{
  inputs = { nixpkgs.url = "github:nixos/nixpkgs"; };

  outputs = { self, nixpkgs }:
    let pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      packages.x86_64-linux.hello = pkgs.hello;
      devShell.x86_64-linux = pkgs.mkShell { buildInputs = [
        pkgs.gnumake
        pkgs.git
        pkgs.coreutils
        pkgs.poetry
        pkgs.jq
      ]; };
    };
}
