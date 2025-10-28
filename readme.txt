to run command do


echo "Hola, ¿cómo estás?" | piper --model voices/es_MX-claude-high.onnx --output-file hola.wav




to getserver running. From the current direcoty SpanishTTS
python3 server.py
docker run -it -p 5500:5000 libretranslate/libretranslate:latest

go to

http://localhost:5500/piper/
