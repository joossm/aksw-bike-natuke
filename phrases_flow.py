# %%
import pandas as pd

path = './data/'

# %%
texts_df = pd.read_parquet('{}phrases-output-final.parquet'.format(path))
# %%

# add text and phrases text to the same column
texts_df['phrases'] = texts_df['text'] + ' ' + texts_df['phrases']
texts_df['phrases'] = texts_df['phrases'].apply(lambda x: x.replace('\n', ' '))
texts_df['phrases'] = texts_df['phrases'].apply(lambda x: x.replace('No Information', ''))
texts_df['phrases'] = texts_df['phrases'].apply(lambda x: x.replace('No information', ''))
texts_df['phrases'] = texts_df['phrases'].apply(lambda x: x.replace('no Information', ''))
texts_df['phrases'] = texts_df['phrases'].apply(lambda x: x.replace('no information', ''))
texts_df['phrases'] = texts_df['phrases'].apply(lambda x: x.replace("I\'m sorry, I don't see any text or input in your message. Can you please provide me with the text you want me to extract information from?I\'m sorry, I didn\'t receive any input. How can I assist you?", ''))

# %%
def phrases_slicing(x):
    phrases = []
    slices = round(len(x) / 512)
    for i in range(slices):
        if i + 1 == slices:
            phrases.append(x[i * 512:])
        else:
            phrases.append(x[i * 512:(i + 1) * 512])
    return phrases


# %%
texts_df['phrases'] = texts_df['phrases'].apply(phrases_slicing)
print(texts_df)

# %%
texts_df.to_parquet("{}phrases-output-final-phrases.parquet".format(path))
