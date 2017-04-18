import React, {Component} from "react";
import { connect } from 'react-redux';
import {PageHeader, Panel, Badge, Well, Tabs, Tab, Label} from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import * as actions from "../actions";
import BoxVersionList from "./BoxVersionList";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {Link} from "react-router";
import {parsePerms} from "../utils";
import MySpinner from "./MySpinner";


class BoxDetail extends Component {
  componentDidMount() {
    this.props.fetchBox(this.props.boxTag);
  }

  onTabSelect = (eventKey) => {
    if (eventKey === 'info') {
      this.props.router.push(`/boxes/${this.props.boxTag}/`);
    } else if (eventKey === 'versions') {
      this.props.router.push(`/boxes/${this.props.boxTag}/versions/`);
    }
  };

  renderBoxDetails = () => {
    if (!this.props.box) {
      return <MySpinner />;
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
            <ReactMarkdown source={this.props.box.description} />
          </Panel>
        }
      </div>
    );
  };

  renderEditOption = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canEdit) {
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
    if (parsePerms(this.props.box.user_permissions).canDelete) {
      return <a href="#" onClick={this.onBoxDelete}>Delete</a>;
    }
    return null;
  };

  renderNewVersionButton = () => {
    if (!this.props.box) {
      return null;
    }
    if (parsePerms(this.props.box.user_permissions).canPush) {
      return (
          <Link to={`/boxes/${this.props.boxTag}/versions/new/`}
                className='btn btn-success'>
          New version
          </Link>
      );
    }
    return null;
  };

  render() {
    const activeTab = this.props.location.pathname.endsWith('/versions/') ? 'versions' : 'info';
    return (
        <div>
          <PageHeader>{this.props.boxTag}</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          {this.renderEditOption()}
          {' '}
          {this.renderDeleteOption()}
          <Tabs
              id="box-tabs"
              defaultActiveKey={activeTab}
              onSelect={this.onTabSelect}
          >
            <Tab eventKey={'info'} title="Box Info">
              {this.renderBoxDetails()}
            </Tab>
            <Tab eventKey={'versions'} title="Versions">
              {this.renderNewVersionButton()}
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
