to run command do


echo "Hola, ¿cómo estás?" | piper --model voices/es_MX-claude-high.onnx --output-file hola.wav




to getserver running. From the current direcoty SpanishTTS

docker rm -f libretranslate_local
lsof -i :5600
docker pull libretranslate/libretranslate:latest
docker run --platform linux/amd64 --name libretranslate_local -p 5600:5000 -d libretranslate/libretranslate:latest
docker logs libretranslate_local


python3 server.py

go to

http://localhost:5500/piper/


