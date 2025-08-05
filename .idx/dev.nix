# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    (pkgs.python311.withPackages (ps: with ps; [
      pip
      tqdm
      lxml
      ipywidgets
      widgetsnbextension
      boto3
      yfinance
      pandas
      requests
      beautifulsoup4
      pyarrow
      streamlit
      altair
      pillow
      fredapi
      google-generativeai
      tabulate
      firebase-admin
    ]))
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = "streamlit run Home.py --server.port $PORT --server.headless true --server.enableCORS false";
          manager = "web";
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {};
      # Runs when the workspace is (re)started
      onStart = {};
    };
  };
}
