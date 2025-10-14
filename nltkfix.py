import ssl, certifi, nltk

ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

for resource in [
    "punkt",
    "punkt_tab",
    "averaged_perceptron_tagger",
    "averaged_perceptron_tagger_eng",
]:
    try:
        (
            nltk.data.find(f"tokenizers/{resource}")
            if "punkt" in resource
            else nltk.data.find(f"taggers/{resource}")
        )
        print(f"✅ {resource} already installed.")
    except LookupError:
        print(f"⬇️  Downloading {resource} ...")
        nltk.download(resource)

print("\n🎉 All NLTK models installed successfully!")
