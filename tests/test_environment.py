import os
import tempfile

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer


def test_csv_write_read():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.csv")

        df = pd.DataFrame({
            "id": [1, 2, 3],
            "value": [10.5, 20.5, 30.5],
        })

        df.to_csv(path, index=False)
        df_read = pd.read_csv(path)

        pd.testing.assert_frame_equal(df, df_read)


def test_parquet_write_read():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.parquet")

        df = pd.DataFrame({
            "id": [1, 2, 3],
            "value": [10.5, 20.5, 30.5],
        })

        df.to_parquet(path, index=False)
        df_read = pd.read_parquet(path)

        pd.testing.assert_frame_equal(df, df_read)


def test_labeled_figure():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_figure.png")

        x = np.arange(5)
        y = x ** 2

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel("Test X")
        ax.set_ylabel("Test Y")
        ax.set_title("Task 02.5 Environment Test")
        fig.savefig(path)
        plt.close(fig)

        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def test_coordinate_transformation():
    import pyproj

    proj_data = os.path.join(
        os.environ["CONDA_PREFIX"],
        "Library",
        "share",
        "proj",
    )

    pyproj.datadir.set_data_dir(proj_data)

    transformer = Transformer.from_crs(
        "EPSG:4326",
        "EPSG:3857",
        always_xy=True,
    )

    x, y = transformer.transform(-84.5, 42.7)

    assert np.isfinite(x)
    assert np.isfinite(y)


def test_deterministic_output():
    a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    result1 = np.mean(a ** 2)
    result2 = np.mean(a ** 2)

    assert result1 == result2
