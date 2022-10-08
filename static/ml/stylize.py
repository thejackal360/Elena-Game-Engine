import torch
from .transformer import TransformerNetwork
# import cv2
import numpy as np
from torchvision import transforms

# Preprocessing ~ Image to Tensor


def itot(img, max_size=None):
    # Rescale the image
    if (max_size is None):
        itot_t = transforms.Compose([
            # transforms.ToPILImage(),
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.mul(255))
        ])
    else:
        H, W, C = img.shape
        image_size = tuple([int((float(max_size) / max([H, W]))*x)
                            for x in [H, W]])
        itot_t = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(image_size),
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.mul(255))
        ])

    # Convert image to tensor
    tensor = itot_t(img)

    # Add the batch_size dimension
    tensor = tensor.unsqueeze(dim=0)
    return tensor


# Preprocessing ~ Tensor to Image
def ttoi(tensor):
    # Add the means
    # ttoi_t = transforms.Compose([
    #    transforms.Normalize([-103.939, -116.779, -123.68],[1,1,1])])

    # Remove the batch_size dimension
    tensor = tensor.squeeze()
    # img = ttoi_t(tensor)
    img = tensor.cpu().numpy()

    # Transpose from [C, H, W] -> [H, W, C]
    img = img.transpose(1, 2, 0)
    return img


# def transfer_color(src, dest):
#     """
#     Transfer Color using YIQ colorspace. Useful in preserving
#     colors in style transfer.
#     This method assumes inputs of shape [Height, Width, Channel]
#     in BGR Color Space
#     """
#     src, dest = src.clip(0, 255), dest.clip(0, 255)

#     # Resize src to dest's size
#     H, W, _ = src.shape
#     dest = cv2.resize(dest, dsize=(W, H), interpolation=cv2.INTER_CUBIC)

#     # 1 Extract the Destination's luminance
#     dest_gray = cv2.cvtColor(dest, cv2.COLOR_BGR2GRAY)

#     # 2 Convert the Source from BGR to YIQ/YCbCr
#     src_yiq = cv2.cvtColor(src, cv2.COLOR_BGR2YCrCb)

#     # 3 Combine Destination's luminance and Source's IQ/CbCr
#     src_yiq[..., 0] = dest_gray

#     # 4 Convert new image from YIQ back to BGR
#     return cv2.cvtColor(src_yiq, cv2.COLOR_YCrCb2BGR).clip(0, 255)


def normalize(x):
    return np.array((x - np.min(x)) / (np.max(x) - np.min(x)))


def stylize(content_image,
            style="udnie"):
    # Device
    device = ("cuda" if torch.cuda.is_available() else "cpu")

    style_transform_path = "./static/ml/transforms/udnie.pth"
    if style == 'udnie':
        pass
    elif style == 'lazy':
        style_transform_path = "./static/ml/transforms/lazy.pth"
    elif style == 'mosaic':
        style_transform_path = "./static/ml/transforms/mosaic.pth"
    elif style == 'van Gogh':
        style_transform_path = "./static/ml/transforms/starry.pth"
    elif style == 'wave':
        style_transform_path = "./static/ml/transforms/wave.pth"
    elif style == 'bayanihan':
        style_transform_path = "./static/ml/transforms/bayanihan.pth"
    elif style == 'ghoul':
        style_transform_path = "./static/ml/transforms/tokyo_ghoul.pth"
    else:
        style_transform_path = './static/ml/transforms/mosaic'

    # Load Transformer Network
    net = TransformerNetwork()
    net.load_state_dict(torch.load(style_transform_path,
                                   map_location=torch.device('cpu')))
    net = net.to(device)

    with torch.no_grad():
        torch.cuda.empty_cache()
        content_tensor = itot(content_image).to(device)
        generated_tensor = net(content_tensor)
        generated_image = ttoi(generated_tensor.detach())
    return normalize(generated_image)


if __name__ == '__main__':
    stylize("images/alex.jpeg", style='tokyo')
