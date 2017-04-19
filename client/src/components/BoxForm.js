import React, {Component} from "react";
import {Button} from "react-bootstrap";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import MySubmitButton from "./MySubmitButton";


class BoxForm extends Component {
  render() {
    return (
        <form onSubmit={this.props.onSubmit}>
          <MyFormError model="box" />

          <MyFormField
              model='box.name'
              type='text'
              label='Name *'
          />
          <MyFormField
              model='box.short_description'
              type='text'
              label='Short description'
          />
          <MyFormField
              model='box.description'
              type='textarea'
              label='Description'
              rows='10'
              helpText="You can use Markdown here"
          />
          <MyFormField
              model='box.visibility'
              type='select'
              label='Visibility'
              items={[
                {value: 'PT', label: 'Private'},
                {value: 'PC', label: 'Public'},
              ]}
          />

          <MySubmitButton
              title={this.props.submitTitle}
              pendingTitle={this.props.submitPendingTitle}
              pending={this.props.pending}
          />
          {' '}
          <Button
              bsStyle="link"
              onClick={this.props.onCancel}
          >
            Cancel
          </Button>
        </form>
    );
  }
}

export default BoxForm;
