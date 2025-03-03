# -*- coding: utf-8 -*-
# Copyright (C) 2018-2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import logging as log

from functools import partial
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from openvino._pyopenvino import NodeFactory as _NodeFactory

from openvino.runtime import Node, Output

from openvino.runtime.exceptions import UserInputError

DEFAULT_OPSET = "opset13"


class NodeFactory(object):
    """Factory front-end to create node objects."""

    def __init__(self, opset_version: str = DEFAULT_OPSET) -> None:
        """Create the NodeFactory object.

        :param      opset_version:  The opset version the factory will use to produce ops from.
        """
        self.factory = _NodeFactory(opset_version)

    def create(
        self,
        op_type_name: str,
        arguments: Optional[List[Union[Node, Output]]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Node:
        """Create node object from provided description.

        The user does not have to provide all node's attributes, but only required ones.

        :param      op_type_name:  The operator type name.
        :param      arguments:     The operator arguments.
        :param      attributes:    The operator attributes.

        :return:   Node object representing requested operator with attributes set.
        """
        if arguments is None and attributes is None:
            node = self.factory.create(op_type_name)
            return node

        if arguments is None and attributes is not None:
            raise UserInputError(f'Error: cannot create "{op_type_name}" op without arguments.')

        if attributes is None:
            attributes = {}

        assert arguments is not None

        arguments = self._arguments_as_outputs(arguments)
        node = self.factory.create(op_type_name, arguments, attributes)

        return node

    def add_extension(self, lib_path: Union[Path, str]) -> None:
        """Add custom operations from extension library.

        Extends operation types available for creation by operations
        loaded from prebuilt C++ library. Enables instantiation of custom
        operations exposed in that library without direct use of
        operation classes. Other types of extensions, e.g. conversion
        extensions, if they are exposed in the library, are ignored.

        In case if an extension operation type from a library match
        one of existing operations registered before (from the standard
        OpenVINO opset or from another extension loaded earlier), a new
        operation overrides an old operation.

        Version of an operation is ignored: an operation with a given type and
        a given version/opset will override operation with the same type but
        different version/opset in the same NodeFactory instance.
        Use separate libraries and NodeFactory instances to differentiate
        versions/opsets.

        :param      lib_path:  A path to the library with extension.
        """
        self.factory.add_extension(lib_path)

    @staticmethod
    def _arguments_as_outputs(arguments: List[Union[Node, Output]]) -> List[Output]:
        outputs = []
        for argument in arguments:
            if issubclass(type(argument), Output):
                outputs.append(argument)
            else:
                outputs.extend(argument.outputs())
        return outputs
