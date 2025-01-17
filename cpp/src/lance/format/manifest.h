//  Copyright 2022 Lance Authors
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#pragma once

#include <arrow/buffer.h>
#include <arrow/io/api.h>
#include <arrow/result.h>

#include <memory>

#include "lance/arrow/dataset.h"
#include "lance/format/data_fragment.h"

namespace lance::format {

namespace pb {
class Manifest;
}

class Schema;

/// \brief Manifest.
///
///  * Schema.
///  * Dataset Version and file position of the version auxiliary data.
///  * Fragments.
///
class Manifest final {
 public:
  Manifest() = default;

  /// Construct a Manifest with the schema.
  ///
  /// \param schema the dataset schema.
  explicit Manifest(std::shared_ptr<Schema> schema);

  /// Construct a Manifest with specific version.
  ///
  /// \param schema full dataset schema.
  /// \param fragments a list of fragments containing data files.
  /// \param version a specific version.
  Manifest(std::shared_ptr<Schema> schema,
           std::vector<std::shared_ptr<DataFragment>> fragments,
           uint64_t version);

  /// Move constructor.
  Manifest(Manifest&& other) noexcept;

  /// Copy constructor.
  Manifest(const Manifest& other) noexcept;

  ~Manifest() = default;

  /// Parse a Manifest from input file at the offset.
  static ::arrow::Result<std::shared_ptr<Manifest>> Parse(
      const std::shared_ptr<::arrow::io::RandomAccessFile>& in, int64_t offset);

  /// Parse a Manifest from a buffer.
  static ::arrow::Result<std::shared_ptr<Manifest>> Parse(
      const std::shared_ptr<::arrow::Buffer>& buffer);

  /// Convert to protobuf.
  pb::Manifest ToProto() const;

  /// Get schema of the dataset.
  const std::shared_ptr<Schema>& schema() const;

  /// Returns the version number.
  uint64_t version() const;

  /// The file position of the version auxiliary data.
  uint64_t version_aux_data_position() const;

  void SetVersionAuxDataPosition(uint64_t pos);

  /// Get the fragments existed in this version of dataset.
  const std::vector<std::shared_ptr<DataFragment>>& fragments() const;

  /// Append more fragments to the dataset.
  void AppendFragments(const std::vector<std::shared_ptr<DataFragment>>& fragments);

 private:
  /// Table schema.
  std::shared_ptr<Schema> schema_;

  uint64_t version_ = 0;

  /// File location of the version aux data.
  std::optional<uint64_t> version_aux_data_position_ = std::nullopt;

  /// Data fragments in this dataset.
  std::vector<std::shared_ptr<DataFragment>> fragments_;

  explicit Manifest(const lance::format::pb::Manifest& pb);
};

}  // namespace lance::format
