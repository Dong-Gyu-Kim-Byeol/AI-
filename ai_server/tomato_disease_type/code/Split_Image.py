import PIL.Image

def split_image(image, row_split_count, column_split_count):
    assert image is not None
    assert isinstance(image, PIL.Image.Image)

    assert row_split_count is not None
    assert isinstance(row_split_count, int)
    assert row_split_count is not 0

    assert column_split_count is not None
    assert isinstance(column_split_count, int)
    assert column_split_count is not 0

    image_width = image.size[0] # width
    image_height = image.size[1] # height

    split_row_im_list = []
    split_row_image_height = int(image_height / row_split_count)
    area_row = [0, None, image_width, None]

    for height in range(0, image_height, split_row_image_height):
        area_row[1] = height
        area_row[3] = height + split_row_image_height
        if area_row[3] > image_height:
            break

        split_row_im_list.append(image.crop(area_row))

    split_image_list = []
    split_column_image_width = int(image_width / column_split_count)
    area_column = [None, 0, None, split_row_image_height]

    for split_row_im in split_row_im_list:
        for width in range(0, image_width, split_column_image_width):
            area_column[0] = width
            area_column[2] = width + split_column_image_width
            if area_column[2] > image_width:
                break

            split_image_list.append(split_row_im.crop(area_column))

    return split_image_list


# image = PIL.Image.open('test.png')

# split_image_list = split_image(image, 3, 3)

# for i in range(len(split_image_list)): #파일명 저장
#     split_image_list[i].save((f'tomato_{str(i)}.png'))