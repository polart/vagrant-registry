import React, {Component} from "react";
import {connect} from "react-redux";
import {Button, PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import MyFormField from "./MyFormField";
import MyFormError from "./MyFormError";
import {Link} from "react-router";


class BoxEditPage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
      return;
    }
    this.props.setFormData('box', this.props.box);
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.editBox(this.props.tag, this.props.form.data);
  };

  render() {
    return (
        <div>
          <PageHeader>Edit box</PageHeader>
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
              Edit
            </Button>
            {' '}
            <Link to={`/boxes/${this.props.tag}/`}>Cancel</Link>
          </form>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName} = props.router.params;
  const tag = `${username}/${boxName}`;
  const box = state.entities.boxes[tag];
  return {
    myUsername: state.myUsername,
    form: state.forms.box,
    tag,
    box,
  }
}

export default connect(mapStateToProps, {
  editBox: actions.editBox,
  setFormData: actions.form.setData,
})(BoxEditPage)
