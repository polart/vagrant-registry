import React, {Component} from "react";
import {Button} from "react-bootstrap";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MySubmitButton from "./MySubmitButton";


class BoxVersionForm extends Component {
  render() {
    return (
        <form onSubmit={this.props.onSubmit}>
          <MyFormError model="boxVersion" />
          <MyFormField
              model='boxVersion.version'
              type='text'
              label='Version *'
          />
          <MyFormField
              model='boxVersion.changes'
              type='textarea'
              label='Changes'
              rows='10'
              helpText="You can use Markdown here"
          />

          <Button
              bsStyle="link"
              onClick={this.props.onCancel}
          >
            Cancel
          </Button>
          {' '}
          <MySubmitButton
              title={this.props.submitTitle}
              pendingTitle={this.props.submitPendingTitle}
              pending={this.props.pending}
          />
        </form>
    );
  }
}

export default BoxVersionForm;
