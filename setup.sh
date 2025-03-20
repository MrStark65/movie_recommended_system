import streamlit

mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = false\n\
\n\
"  > ~/.streamlit/config.toml
