import cv2
import matplotlib.pyplot as plt
from ebuy.data_collection.misc import read_yaml
import os
import pandas as pd


folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
img_path = config['download_path']
check_file = img_path + 'labels.csv'
img_size = (1200, 1440)
features = ['Disc', 'Disc (Under)', 'Case', 'Manual', 'Screen', 'Multiple Discs', 'Multiple Cases']
feature_count = len(features)

# For Multiple case/disc scenarios, we should go back and double check if the correct case/disc is there. Label apt.

def get_response():
    res = ""
    while len(res) != feature_count and res != '0':
        res = input('Classification String: \n')
        if res.lower() == 'exit':
            return 'exit'
    return res


def open_csv(check_file, img_list):
    if os.path.exists(check_file):
        print('Opening existing csv file.')
        df = pd.read_csv(check_file, index_col=0)
    else:
        print('Creating new dataframe to begin. Next time you can pick up from a data file.')
        df = pd.DataFrame({'img_name_index': img_list})
        df = df.set_index('img_name_index')
        df['img_name'] = df.index
        df['features'] = 'missing'
        print(df.columns)
    return df


def write_df(df, img, val):
    df.loc[img, 'features'] = val
    return df


def write_csv(df, check_file):
    df.to_csv(check_file)
    return None


def exit_process(df, check_file):
    write_csv(df, check_file)
    plt.close()
    print('Writing to data file and exiting.\n')
    needed_imgs = list(df[df.features == 'missing'].img_name)
    print(f'Only {len(needed_imgs)} to go!')
    exit(1)


if __name__ == '__main__':
    imgs = os.listdir(img_path)
    df = open_csv(check_file, imgs)
    needed_imgs = list(df[df.features == 'missing'].img_name)
    needed_imgs = [img for img in needed_imgs]

    plt.ion()
    fig = plt.figure()
    ax = plt.subplot(1, 1, 1)
    fig.show()  # show the window (figure will be in foreground, but the user may move it to background)

    if not needed_imgs:
        print('No images needed. Exiting.')
        exit(1)

    for img in needed_imgs:
        print(img)
        try:
            im = cv2.imread(img_path + img)
            im_resized = cv2.resize(im, img_size, interpolation=cv2.INTER_LINEAR)
            plt.imshow(cv2.cvtColor(im_resized, cv2.COLOR_BGR2RGB))

            res = get_response()
        except cv2.error:
            print(f'Could not retrieve image {img}. Filling features as null (all 0\'s')
            res = '0'*feature_count

        fig.canvas.flush_events()

        if res == 'exit':
            break
        write_df(df, img, res)
    exit_process(df, check_file)
