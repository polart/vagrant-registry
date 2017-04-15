import React, {Component} from "react";
import {connect} from "react-redux";
import {isArray} from "lodash";
import {Alert} from "react-bootstrap";


class MyFormError extends Component {
  renderErrors() {
    let errors = this.props.errors;
    if (!isArray(errors)) {
      errors = [errors];
    }

    return errors.map((error, index) => {
      return (
          <Alert bsStyle="danger" key={index}>{error}</Alert>
      );
    });
  }

  render() {
    if (!this.props.errors) {
      return null;
    }
    return <div>{this.renderErrors()}</div>;
  }
}

function mapStateToProps(state, props) {
  const allErrors = state.forms[props.model].errors;
  const errors = allErrors.non_field_errors || allErrors.detail;
  return {
    errors,
  }
}

export default connect(mapStateToProps)(MyFormError)
