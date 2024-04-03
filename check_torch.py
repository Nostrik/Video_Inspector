import torch


def check_torch():
    check = torch.cuda.is_available()
    return check


# if __name__ == "__main__":
#     print(check_torch())
