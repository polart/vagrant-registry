import React, {Component} from "react";
import {connect} from "react-redux";
import { omit, isArray } from 'lodash';
import * as actions from "../actions";
import {ControlLabel, FormControl, FormGroup, HelpBlock} from "react-bootstrap";


const OMIT_PROPS = [
  'model',
  'type',
  'value',
  'errors',
  'fieldChange',
  'items',
];

class MyFormField extends Component {
  onChange = (e) => {
    this.props.fieldChange(this.props.model, e.target.value);
  };

  renderErrors = () => {
    if (!this.props.errors) {
      return null;
    }
    let errors = this.props.errors;
    if (!isArray(errors)) {
      errors = [errors];
    }
    return errors.map((error, index) => {
      return <HelpBlock key={index}>{error}</HelpBlock>;
    });
  };

  renderInput = () => {
    const fieldProps = omit(this.props, OMIT_PROPS);
    if (this.props.type === 'textarea') {
      return (
        <FormControl
            componentClass='textarea'
            value={this.props.value}
            onChange={this.onChange}
            { ...fieldProps }
        />
      );
    }
    if (this.props.type === 'select') {
      const options = this.props.items.map((option) => {
        return (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
        );
      });
      return (
        <FormControl
            componentClass='select'
            value={this.props.value}
            onChange={this.onChange}
            { ...fieldProps }
        >
          {options}
        </FormControl>
      );
    }
    return (
        <FormControl
            type={this.props.type}
            value={this.props.value}
            onChange={this.onChange}
            { ...fieldProps }
        />
    );
  };

  getValidationState = () => {
    if (this.props.errors) {
      return 'error';
    }
    return null;
  };

  render() {

    return (
        <FormGroup
            controlId={this.props.model}
            validationState={this.getValidationState()}
        >
          <ControlLabel>{this.props.label}</ControlLabel>
          {this.renderInput()}
          {this.renderErrors()}
        </FormGroup>
    );
  }
}

function mapStateToProps(state, props) {
  const modelPath = props.model.split('.');
  const form = state.forms[modelPath[0]];
  return {
    value: form.data[modelPath[1]],
    errors: form.errors[modelPath[1]],
  }
}

export default connect(mapStateToProps, {
  fieldChange: actions.form.fieldChange,
})(MyFormField)
