# Copyright 2022 Lance Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

import lance
from lance import LanceFileFormat, dataset
from lance.util import cd


def test_simple_round_trips(tmp_path: Path):
    table = pa.Table.from_pandas(
        pd.DataFrame({"label": [123, 456, 789], "values": [22, 33, 2.24]})
    )
    pa.dataset.write_dataset(table, tmp_path / "test.lance", format=LanceFileFormat())

    assert (tmp_path / "test.lance").exists()

    ds = dataset(str(tmp_path / "test.lance"))
    actual = ds.to_table()

    assert table == actual


def test_head(tmp_path: Path):
    table = pa.Table.from_pandas(
        pd.DataFrame({"label": [123, 456, 789], "values": [22, 33, 2.24]})
    )
    pa.dataset.write_dataset(table, tmp_path / "test.lance", format=LanceFileFormat())
    ds = dataset(str(tmp_path / "test.lance"))
    actual = ds.head(2)
    assert table[:2] == actual


def test_write_categorical_values(tmp_path: Path):
    df = pd.DataFrame({"label": ["cat", "cat", "dog", "person"]})
    df["label"] = df["label"].astype("category")
    table = pa.Table.from_pandas(df)
    ds.write_dataset(table, tmp_path / "test.lance", format=LanceFileFormat())

    assert (tmp_path / "test.lance").exists()

    actual = dataset(str(tmp_path / "test.lance")).to_table()
    assert table == actual


def test_write_dataset(tmp_path: Path):
    table = pa.Table.from_pandas(
        pd.DataFrame(
            {
                "label": [123, 456, 789],
                "values": [22, 33, 2.24],
                "split": ["a", "b", "a"],
            }
        )
    )
    ds.write_dataset(table, tmp_path, partitioning=["split"], format=LanceFileFormat())

    part_dirs = [d.name for d in tmp_path.iterdir()]
    assert set(part_dirs) == set(["a", "b"])
    part_a = list((tmp_path / "a").glob("*.lance"))[0]
    actual = dataset(part_a).to_table()
    assert actual == pa.Table.from_pandas(
        pd.DataFrame({"label": [123, 789], "values": [22, 2.24]})
    )


def test_write_dataset_with_metadata(tmp_path: Path):
    table = pa.Table.from_pylist(
        [{"a": 1}, {"a": 2}], metadata={"k1": "v1", "k2": "v2"}
    )
    ds.write_dataset(table, tmp_path / "test.lance", format=LanceFileFormat())

    actual = dataset(str(tmp_path / "test.lance")).to_table()
    schema: pa.Schema = actual.schema
    assert schema.metadata[b"k1"] == b"v1"
    assert schema.metadata[b"k2"] == b"v2"


def test_write_versioned_dataset(tmp_path: Path):
    table1 = pa.Table.from_pylist([{"a": 1, "b": 2}])
    base_dir = tmp_path / "test"
    lance.write_dataset(table1, base_dir)

    assert (base_dir / "data").exists()
    assert (base_dir / "_latest.manifest").exists()
    assert (base_dir / "_versions/1.manifest").exists()

    table2 = pa.Table.from_pylist([{"a": 100, "b": 200}])
    lance.write_dataset(table2, base_dir, mode="append")
    assert (base_dir / "_versions/2.manifest").exists()

    table3 = pa.Table.from_pylist([{"a": -100, "b": -200}])
    lance.write_dataset(table3, base_dir, mode="overwrite")
    assert (base_dir / "_versions/3.manifest").exists()

    dataset = lance.dataset(base_dir, version=1)
    assert table1 == dataset.to_table()
    assert dataset.version["version"] == 1
    assert dataset.latest_version()["version"] == 3

    dataset = lance.dataset(base_dir, version=2)
    full_table = pa.Table.from_pylist([{"a": 1, "b": 2}, {"a": 100, "b": 200}])
    assert full_table == dataset.to_table()

    assert dataset.version["version"] == 2
    assert dataset.latest_version()["version"] == 3
    assert len(dataset.versions()) == 3

    dataset = lance.dataset(base_dir)
    assert dataset.to_table() == table3
    assert dataset.version["version"] == 3
    assert dataset.latest_version()["version"] == 3
    assert len(dataset.versions()) == 3


def test_asof(tmp_path: Path):
    table1 = pa.Table.from_pylist([{"a": 1, "b": 2}])
    base_dir = tmp_path / "test"
    lance.write_dataset(table1, base_dir)

    test_ts = datetime.now()
    time.sleep(1)

    table2 = pa.Table.from_pylist([{"a": 100, "b": 200}])
    lance.write_dataset(table2, base_dir, mode="append")

    dataset = lance.dataset(base_dir, asof=test_ts)
    assert dataset.version["version"] == 1


def test_open_local_path(tmp_path: Path):
    table = pa.Table.from_pylist([{"a": 1, "b": 2}])
    base_dir = tmp_path / "local_path"
    lance.write_dataset(table, base_dir)

    with cd(tmp_path):
        ds = lance.dataset("./local_path")
        assert ds.to_table() == table

    with cd(tmp_path):
        ds = lance.dataset("local_path")
        assert ds.to_table() == table

    ds = lance.dataset(base_dir.absolute())
    assert ds.to_table() == table
