import fire
import downloads_corridor_google_image
import get_sparse_point
import add_gps


def total_dwld():
    downloads_corridor_google_image.run()


def sparse():
    get_sparse_point.run()


def assign_gps():
    add_gps.run()


if __name__ == '__main__':
    fire.Fire({
        'total_dwld': total_dwld,
        'sparse': sparse,
        'assign_gps': assign_gps,
    })
