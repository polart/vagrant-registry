import React, {Component} from "react";
import {connect} from "react-redux";
import {Button, PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";


class BoxCreatePage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
    }
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBox(this.props.myUsername, this.props.form.data);
  };

  render() {
    return (
        <div>
          <PageHeader>Create new box</PageHeader>
          <form
              onSubmit={this.onSubmit}
          >
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

            <Button
                bsStyle="success"
                type="submit"
                disabled={this.props.form.pending}
            >
              Create
            </Button>
          </form>
        </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    myUsername: state.myUsername,
    form: state.forms.box,
  }
}

export default connect(mapStateToProps, {
  createBox: actions.createBox,
})(BoxCreatePage)
