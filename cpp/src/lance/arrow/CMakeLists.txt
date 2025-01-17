#  Copyright 2022 Lance Authors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


# Arrow integration

add_library(
        arrow
        OBJECT
        dataset.cc
        dataset_ext.h
        file_lance.cc
        file_lance_ext.h
        fragment.cc
        fragment.h
        hash_merger.cc
        hash_merger.h
        scanner.cc
        stl.h
        type.cc
        type.h
        updater.cc
        utils.cc
        utils.h
)
target_include_directories(arrow SYSTEM PRIVATE ${Protobuf_INCLUDE_DIR})

add_lance_test(api_test)
add_lance_test(arrow_dataset_test)
add_lance_test(dataset_test)
add_lance_test(fragment_test)
add_lance_test(hash_merger_test)
add_lance_test(scanner_test)
add_lance_test(type_test)
add_lance_test(updater_test)
add_lance_test(utils_test)
add_lance_test(writer_test)
