import React, {Component} from "react";
import { connect } from 'react-redux';
import {PageHeader, Panel, Badge, Well, Tabs, Tab} from 'react-bootstrap';
import * as actions from "../actions";
import BoxVersionList from "./BoxVersionList";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {Link} from "react-router";


class BoxDetail extends Component {
  componentDidMount() {
    this.props.fetchBox(this.props.boxTag);
  }

  renderBoxDetails = () => {
    if (!this.props.box) {
      return <div>Loading...</div>
    }

    return (
      <div>
        <Badge>{this.props.box.pulls} pulls</Badge>
        <Panel header="Quick start">
          <Well bsSize="small">
            <p>vagrant init {this.props.boxTag} {window.location.origin}/{this.props.boxTag}</p>
            <p>vagrant up</p>
          </Well>
        </Panel>
        {!!this.props.box.short_description.length &&
          <Panel header="Short description">
            {this.props.box.short_description}
          </Panel>
        }
        {!!this.props.box.description.length &&
          <Panel header="Description">
            {this.props.box.description}
          </Panel>
        }
      </div>
    );
  };

  renderEditOption = () => {
    if (!this.props.box) {
      return null;
    }
    if (this.props.box.user_permissions === '*') {
      return <Link to={`/boxes/${this.props.boxTag}/edit/`}>Edit</Link>;
    }
    return null;
  };

  onBoxDelete = (e) => {
    e.preventDefault();
    // TODO: would be good to use custom Confirm dialog
    if (window.confirm(`Are you sure you want to delete box ${this.props.boxTag}?`)) {
      this.props.deleteBox(this.props.boxTag);
    }
  };

  renderDeleteOption = () => {
    if (!this.props.box) {
      return null;
    }
    if (this.props.box.user_permissions === '*') {
      return <a href="#" onClick={this.onBoxDelete}>Delete</a>;
    }
    return null;
  };

  render() {
    return (
        <div>
          <PageHeader>{this.props.boxTag}</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          {this.renderEditOption()}
          {' '}
          {this.renderDeleteOption()}
          <Tabs id="box-tabs">
            <Tab eventKey={1} title="Box Info">
              {this.renderBoxDetails()}
            </Tab>
            <Tab eventKey={2} title="Versions">
              <BoxVersionList boxTag={this.props.boxTag} router={this.props.router} />
            </Tab>
          </Tabs>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  const {username, boxName} = props.params;
  const boxTag = `${username}/${boxName}`;
  return {
    box: state.entities.boxes[boxTag],
    boxTag,
  }
}

export default connect(mapStateToProps, {
  fetchBox: actions.loadBox,
  deleteBox: actions.deleteBox,
})(BoxDetail)
